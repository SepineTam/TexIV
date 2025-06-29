from texiv import TexIV

texiv = TexIV()

if __name__ == "__main__":
    content = "随着中国进入了21世纪，乘着中国快速发展的东风，数字中国建设如火如荼地展开。数字化转型是数字中国建设的核心内容，是推动经济高质量发展的重要动力。新质生产力是数字化转型的必然产物，是推动数字中国建设的重要力量。"
    keywords = ["数字化", "智能化", "信息素养"]
    print(info := texiv.texiv_it(content, keywords))
